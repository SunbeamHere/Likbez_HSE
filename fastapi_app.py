import logging
from fastapi import FastAPI, Request, status
from pydantic import BaseModel, ValidationError, root_validator
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional

#consts
errMsg_idNotExist = "Incorrect ID"
errMsg_IncorrectKind = "Incorrect dog kind"
validKinds = ["terrier", "bulldog", "dalmatian"]
maxId = 0

#basic data structure

class RequestBaseModel(BaseModel):
    @root_validator(pre=True)
    def body_params_case_insensitive(cls, values: dict):
        for field in cls.__fields__:
            in_fields = list(filter(lambda f: f.lower() == field.lower(), values.keys()))
            for in_field in in_fields:
                values[field] = values.pop(in_field)

        return values

class Dog(RequestBaseModel):

    name: str
    pk: Optional[int] = -1
    kind: str

#inmemory database:)
dogs = []

#api
app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.get("/")
def get_root():
    return ""

@app.post("/post")
def read_post_root():
    return ''

@app.get("/dog")
def read_dogs(kind:str = ''):
    result = []
    if not(kind == '') and not(kind in validKinds):
        raise HTTPException(status_code=422, detail=errMsg_IncorrectKind)
    for d in dogs:
        if kind == '':
            result.append(d)
        else:
            if d.kind == kind:
                result.append(d)
    return result

@app.get("/dog/{pk}")
def read_dogs(pk):

    if pk.isdigit():
        result = [x for x in dogs if x.pk == int(pk)]
    else:
        if pk in validKinds:
            result = [x for x in dogs if x.kind == pk]
        else:
            raise HTTPException(status_code=422, detail=errMsg_IncorrectKind)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail=errMsg_idNotExist)
    return result[0]

@app.post("/dog")
def create_dog(newdog: Dog):

    global maxId
    print(newdog)
    if not(newdog.kind in validKinds):
        raise HTTPException(status_code=422, detail=errMsg_IncorrectKind + " " + newdog.kind)

    if (newdog.pk == -1):
        newdog.pk = maxId
        maxId += 1
    else:
        if (len([x for x in dogs if x.pk == newdog.pk]) != 0):
            raise HTTPException(status_code=404, detail=errMsg_idNotExist)

    if (newdog.pk >= maxId):
        maxId = newdog.pk + 1

    dogs.append(newdog)
    return newdog

@app.patch("/dog/{pk}")
def update_dog(pk: int, u_dog: Dog):

    print(u_dog)
    result = ""
    
    if (len([x for x in dogs if x.pk == pk]) == 0):
        raise HTTPException(status_code=404, detail=errMsg_idNotExist)

    if not(u_dog.kind in validKinds):
        raise HTTPException(status_code=422, detail=errMsg_IncorrectKind + str(u_dog))
    
    
    for d in dogs:
        if d.pk == pk:
            d.name = u_dog.name
            d.kind = u_dog.kind
            result = d
            break
    return result
