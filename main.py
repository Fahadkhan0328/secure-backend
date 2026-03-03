import jwt
import zarr
import numpy as np
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Your existing verify_token function stays here ---
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        unverified_claims = jwt.decode(token, options={"verify_signature": False})
        issuer = unverified_claims.get("iss")
        jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
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
        
        # 2. THE FIX: Act as a sniper and fetch the exact metadata arrays!
        meta_dict = {}
        target_metadata = ["plaintext", "rin", "rout"]
        
        for meta_name in target_metadata:
            try:
                # Point EXACTLY to the sub-folders we discovered
                meta_url = f"hf://datasets/DLSCA/ascad-v1-fk/metadata/{meta_name}"
                meta_array = zarr.open_array(meta_url, mode='r')
                
                # Grab the exact value for this specific trace
                val = meta_array[trace_index]
                meta_dict[meta_name] = np.array(val).tolist()
            except Exception as e:
                meta_dict[meta_name] = f"Unavailable"
        
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