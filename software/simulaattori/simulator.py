from fastapi import FastAPI
import math

app = FastAPI()

# JSON-safe funktio säilyttää inf ja nan
def json_safe(v):
    if v is None:
        return None  # VAARA / ei dataa
    if isinstance(v, float):
        if math.isinf(v):
            return "inf"   # ei estettä
        if math.isnan(v):
            return "nan"   # liian lähellä
    return v  # normaali float


# Oletusarvot
depth_data = {
    "left": float("inf"),    # alussa vapaa tie
    "center": float("inf"),
    "right": float("inf")
}
IO_data = {
    "IO1":1,
    "IO2":0,
    "IO3":0,
    "IO4":0,
    "IO5":0,
}
IMU_data = {
        "roll_deg": float(0.0),     # roll = x
        "pitch_deg": float(0.0),    # pitch = y
        "yaw_deg": float(0.0),      # yaw = z
    }

@app.get("/depth")
def get_depth():
    return {
        "left": json_safe(depth_data["left"]),
        "center": json_safe(depth_data["center"]),
        "right": json_safe(depth_data["right"]),
    }
@app.get("/IO")
def get_IO():
    return{
        
    "IO1":IO_data["IO1"],
    "IO2":IO_data["IO2"],
    "IO3":IO_data["IO3"],
    "IO4":IO_data["IO4"],
    "IO5":IO_data["IO5"],

    }
@app.get("/IMU")
def get_IMU():
    return {
        "roll_deg": IMU_data["roll_deg"],       # x = roll
        "pitch_deg": IMU_data["pitch_deg"],      # y = pitch
        "yaw_deg": IMU_data["yaw_deg"],         # z = yaw/heading
    }


@app.post("/set_depth")
def set_depth(left: str, center: str, right: str):
    def parse(v):
        v_lower = v.lower()
        if v_lower == "nan":
            return float("nan")
        if v_lower == "inf":
            return float("inf")
        if v_lower == "none" or v_lower == "null":
            return None
        return float(v)

    depth_data["left"] = parse(left)
    depth_data["center"] = parse(center)
    depth_data["right"] = parse(right)

    return get_depth()  # palauttaa JSON-safe version

@app.post("/set_IO")
def set_IO(IO1:int,IO2:int,IO3:int,IO4:int,IO5:int):
    def parse(v):
        try:
            int(v)
        except ValueError:
            return 0
        return 1 if v == 1 else 0
           
    IO_data["IO1"] = parse(IO1)        
    IO_data["IO2"] = parse(IO2)
    IO_data["IO3"] = parse(IO3)
    IO_data["IO4"] = parse(IO4)
    IO_data["IO5"] = parse(IO5)
    
    return get_IO()

@app.post("/set_IMU")
def set_IMU(x:float,y:float,z:float):
    IMU_data["roll_deg"] = x
    IMU_data["pitch_deg"] = y
    IMU_data["yaw_deg"] = z
    return get_IMU()