from src.transactionCustomOperation import handle_custom_operation
from sqlalchemy.orm import Session
from src.exceptions import BadReqExpection, DatabaseErrorException, GeneralErrorExcpetion
from src.loggerServices import log_error
from src.constants import ORM_OPERATION_TYPE
from src.models import OperationsList

def wrap_bulk_insert_orm_trx_func(db: Session, mapping_function_list) -> list:
    """
    Executes one or more callables that perform bulk insert operations (like bulk_save_objects)
    and returns their results.
    """
    try:
        result_list = [mp(db) for mp in mapping_function_list]
        db.commit()
        return result_list
    except Exception as e:
        db.rollback()
    return []

async def wrap_async_bulk_insert_orm_trx_func(db: Session, mapping_function_list) -> list:
    """
    Executes one or more async callables that perform bulk insert operations (like bulk_save_objects)
    and returns their results.
    """
    try:
        result_list = []
        for mp in mapping_function_list:
            result = await mp(db)
            result_list.append(result)
        db.commit()
        return result_list
    except Exception as e:
        db.rollback()
        raise e
    return []

# Insert
def wrap_insert_mapping_func(db: Session, mapping_function) -> dict:
    result = mapping_function  
    db.add(result)
    db.flush()
    return result

def wrap_insert_trx(db: Session, mapping_function_list)->list:
    try:
        res = []
        result_list = [wrap_insert_mapping_func(db,mp) for mp in mapping_function_list]
        db.commit()
        for result in result_list:
            db.refresh(result)
            res.append({"id":result.id})
        return res
    except Exception as e:
        db.rollback()
        raise DatabaseErrorException(details=str(e))





# Update

def wrap_update_func(m,f:dict,u:dict,db:Session,isExist:bool):
    if isExist:
            db.query(m).filter_by(**f).update(u)
    else:
        raise Exception("row not found")  # 未找到

def wrap_update_trx(m,f:dict,u:dict,db:Session,isExist:bool):
    if isExist:
        try:
            db.query(m).filter_by(**f).update(u)
            db.commit()
            return True # 返回成功
        except Exception as e:
            db.rollback()
            raise DatabaseErrorException(details=str(e))
    else:
        raise BadReqExpection(details="row not found")  # 未找到



# Delete
def wrap_delete_func(m,f:dict,db:Session,isExist:bool=True):
    if isExist:
            db.query(m).filter_by(**f).delete()
    else:
        raise Exception("row not found")  # 未找到

def wrap_delete_trx(m,f:dict,db:Session,isExist:bool=True):
    if isExist:
        try:
            db.query(m).filter_by(**f).delete()
            db.commit()
            return True # 返回成功
        except Exception as e:
            db.rollback()
            raise DatabaseErrorException(details=str(e))
    else:
        raise BadReqExpection(details="row not found")  # 未找到

def wrap_orm_handler(operations: OperationsList, db: Session):
    """
    Handle multiple ORM operations in a single transaction
    
    Args:
        operations: List of dictionaries with operations
        db: SQLAlchemy database session
        
    Returns:
        List of operation results
        
    Raises:
        DatabaseErrorException if any operation fails
    """
    try:
        results = []
        for operation in operations:
            if operation.get("type") == ORM_OPERATION_TYPE.CUSTOM.value:
                # Handle custom operations
                result = handle_custom_operation(operation, db)
            else:
                # Handle standard ORM operations
                result = do_orm_operation(operation, db)
            results.append(result)

        db.commit()
        return results
    except Exception as e:
        db.rollback()
        log_error(f"Multi-ORM operation error -> {e}")
        raise DatabaseErrorException(details=str(e))


def do_orm_operation(operation: dict, db: Session):
    """
    Perform a single ORM operation without transaction handling
    
    Args:
        operation: Dictionary with operation details
            {
                "model": SQLAlchemy model class,
                "filter": Dictionary of filter conditions,
                "values": Dictionary or Pydantic model of values to update,
                "schema_class": Optional Pydantic model class to validate values,
                "check_exists": Boolean, whether to check if record exists
            }
        db: SQLAlchemy database session
        
    Returns:
        The result of the operation (model instance or True)
        
    Raises:
        Exception if operation fails
    """
    model = operation["model"]
    filter_conditions = operation["filter"]
    values = operation["values"]
    check_exists = operation.get("check_exists", True)
    schema_class = operation.get("schema_class", None)
    operation_type = operation.get("type", ORM_OPERATION_TYPE.UPDATE.value)  # Default to update
    
    # Convert Pydantic model to dict if necessary
    if hasattr(values, 'model_dump'):
        values_dict = values.model_dump()
    elif schema_class and not isinstance(values, dict):
        # Convert to schema class first, then to dict
        schema_instance = schema_class(**values)
        values_dict = schema_instance.model_dump()
    elif isinstance(values, dict):
        values_dict = values
    else:
        raise GeneralErrorExcpetion(f"Values must be a dict or Pydantic model, got {type(values)}")
    
    # Build the query with filter conditions
    query = db.query(model)
    for field, value in filter_conditions.items():
        query = query.filter(getattr(model, field) == value)
    
    # Check if record exists if required
    if check_exists and query.count() == 0:
        raise BadReqExpection(details=f"Record not found for {model.__name__}")
    
    # Perform the operation based on type
    if operation_type == ORM_OPERATION_TYPE.UPDATE.value:
        query.update(values_dict)
        return True
    elif operation_type == ORM_OPERATION_TYPE.DELETE.value:
        query.delete()
        return True
    elif operation_type == ORM_OPERATION_TYPE.INSERT.value:
        new_instance = model(**values_dict)
        db.add(new_instance)
        db.flush()
        return new_instance
    else:
        raise GeneralErrorExcpetion(f"Unknown operation type: {operation_type}")
