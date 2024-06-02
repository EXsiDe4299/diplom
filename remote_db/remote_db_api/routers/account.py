from fastapi import APIRouter, Depends, HTTPException

from core.database.sqlite_database import get_sqlite_session
from core.database.utils import get_session
from core.schemas.account import CreatedAccountScheme, CreateAccountScheme, EditAccountScheme
from middleware.account_middleware import get_user_id, check_account_existing, create_new_account, change_account, \
    account_authentication
from middleware.user_middleware import check_user_existing

account_router = APIRouter()
sqlite_db_dependency = Depends(get_sqlite_session)
db_dependency = Depends(get_session)


@account_router.post("/create", response_model=CreatedAccountScheme, status_code=201)
async def create_account(user_data: CreateAccountScheme, sqlite_session=sqlite_db_dependency,
                         session=db_dependency):
    if not session:
        raise HTTPException(500, detail='Incorrect dbms name')
    user_exists = await check_user_existing(user_data=user_data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(404, detail="Unknown user")

    user_id = await get_user_id(user_data=user_data, sqlite_session=sqlite_session)

    account_exists = await check_account_existing(user_data=user_data, sqlite_session=sqlite_session,
                                                  dbms_name=session.get_bind().name)

    if account_exists:
        raise HTTPException(409, detail="You already have an account")

    new_user = await create_new_account(user_id=user_id, user_data=user_data, sqlite_session=sqlite_session,
                                        session=session)
    await sqlite_session.commit()
    await session.commit()
    return new_user


@account_router.post('/edit')
async def edit_account(account_data: EditAccountScheme, sqlite_session=sqlite_db_dependency, session=db_dependency):
    if not session:
        raise HTTPException(500, detail='Incorrect dbms name')
    user_exists = await check_user_existing(user_data=account_data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(404, detail="Unknown user")

    user_id = await get_user_id(user_data=account_data, sqlite_session=sqlite_session)

    account_exists = await check_account_existing(user_data=account_data, sqlite_session=sqlite_session,
                                                  dbms_name=session.get_bind().name)

    if not account_exists:
        raise HTTPException(404, detail="You don't have an account")

    successful_authentication = await account_authentication(data=account_data, sqlite_session=sqlite_session,
                                                             dbms_name=session.get_bind().name)
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    edited_account = await change_account(user_id=user_id, user_data=account_data, sqlite_session=sqlite_session,
                                          session=session)
    await sqlite_session.commit()
    await session.commit()
    return edited_account
