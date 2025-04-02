from pydantic import BaseModel

class StepOneGenerationResult(BaseModel):
    critical_obstacle_ids: list[str] # list of critical dynamic obstacle ids

class TimeInterval(BaseModel):
    start_time: int
    end_time: int

# include boolean for collision true and false
class StepTwoGenerationResult(BaseModel):
    critical_obstacle_id: str
    critical_interval: TimeInterval
    critical_lanelet_id: str

class StepThreeGenerationResult(BaseModel):
    updated_scenario_dict: dict



