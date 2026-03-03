import jwt
import zarr
import numpy as np
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
security = HTTPBearer() # <-- Added this line

# Update this list with your actual Vercel deployment URL
origins = [
    "http://localhost:5173",
    "https://secure-frontend-indol.vercel.app", # REPLACE with your live Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        # We decode the token to get the Issuer (ISS) URL from Clerk
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
        issuer = unverified_claims.get("iss")
        jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
        
        jwks_client = jwt.PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Verify the signature using Clerk's public key
        payload = jwt.decode(token, signing_key.key, algorithms=["RS256"], options={"verify_aud": False})
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@app.get("/api/leakage-data")
def get_secure_data(trace_index: int = 0, user_data: dict = Depends(verify_token)):
    zarr_url_traces = "hf://datasets/DLSCA/ascad-v1-fk/traces"
    
    try:
        # 1. Fetch the raw electrical wave
        trace_array = zarr.open_array(zarr_url_traces, mode='r')
        trace_slice = trace_array[trace_index, :700]
        trace_data = np.array(trace_slice).astype(float).tolist()
        
        # 2. Fetch the metadata (plaintext, rin, rout)
        meta_dict = {}
        target_metadata = ["plaintext", "rin", "rout"]
        
        for meta_name in target_metadata:
            try:
                meta_url = f"hf://datasets/DLSCA/ascad-v1-fk/metadata/{meta_name}"
                meta_array = zarr.open_array(meta_url, mode='r')
                val = meta_array[trace_index]
                meta_dict[meta_name] = np.array(val).tolist()
            except Exception:
                meta_dict[meta_name] = "Unavailable"
        
        return {
            "status": "success", 
            "dataset": "DLSCA/ascad-v1-fk",
            "trace_index": trace_index,
            "data_preview": trace_data,
            "metadata": meta_dict,
            "message": f"Successfully streamed Trace #{trace_index} AND its secret keys!"
        }
    except Exception as e:
        return {"status": "error", "message": f"Cloud Data Error: {str(e)}"}

# --- THE FIX: Move this block ALL THE WAY TO THE LEFT ---
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)