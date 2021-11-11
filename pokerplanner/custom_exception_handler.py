from rest_framework.views import exception_handler


def get_response(message="", status_code=200):
    """
    Function to normalise the error format 
    """
    return {
        "message": message.title(),
        "status_code": status_code,
    }


def get_error_message(error_dict):
    """
    This function actually check for dict formats and return error messages.
    """
    response = error_dict[next(iter(error_dict))]
    if isinstance(response, dict):
        response = get_error_message(response)
    elif isinstance(response, list):
        response_message = response[0]
        if isinstance(response_message, dict):
            response = get_error_message(response_message)
        else:
            response = response[0]
    return response


def handle_exception(exc, context):
    """
    Custom exception handler, called when any error in DRF is raised.
    """
    # It receives two args -
    #             exc --> Error itself,
    #             context --> any extra data like view in which error raised
    # It passes error through in-built exception handler and fetches a Response object(JSON format).
    # Then data from Response object is checked if - 
    #     instance is list and then further str or dict, respectively for example - ['Invite not found'] ,
    #     ['pokerboard' : {'Invalid pokerboard_id'}]
    #     Similar for when instance is dict
    #     When instance is dict, pokerboard : {'Invalid'} then to get proper error like 'Pokerboard : Invalid',
    #     key i.e Pokerboard is appended to the error message.
    error_response = exception_handler(exc, context)
    if error_response is not None:
        error = error_response.data

        if isinstance(error, list) and error:
            if isinstance(error[0], dict):
                error_response.data = get_response(
                    message=get_error_message(error),
                    status_code=error_response.status_code,
                )

            elif isinstance(error[0], str):
                error_response.data = get_response(
                    message=error[0],
                    status_code=error_response.status_code
                )

        if isinstance(error, dict):
            field = next(iter(dict(error_response.data)))
            error_response.data = get_response(
                message=field + ": " + get_error_message(error),
                status_code=error_response.status_code
            )
    return error_response
