from fastapi import HTTPException, status


class Error(Exception):

    TEACHER_NOT_FOUND_EXCEPTION = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Teacher not found."
    )
    
    PUPIL_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Pupil not found."
    )
    
    PUPIL_ALREADY_IN_GROUP = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Pupil already in group."
    )
    
    LOGIN_EXISTS = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Login already exists."
    )
    
    GROUP_EXISTS = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Group with this name already exists"
    )
    
    GROUP_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Group not found."
    )
    
    UNAUTHORIZED_INVALID = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect login or password."
    )
    
    USER_IP_NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User ip not found."
    )
    
    