# Database connection dependencies

# from typing import Annotated
# from fastapi import APIRouter, Depends, Cookie, Header, HTTPException

# router = APIRouter()


# Dependencies with yield
# that do some extra steps after finishing
# async def get_db():
#     db = DBSession()
#     try:
#         yield db
#     finally:
#         db.close()


# Context manger
# class MySuperContextManger:
#     def __init__(self):
#         self.db = DBSession()

#     def __enter__(self):
#         return self.db

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.db.close()


# async def get_db():
#     with MySuperContextManger() as db:
#         yield db
