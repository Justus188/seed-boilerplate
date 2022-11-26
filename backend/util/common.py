import schemas

responses = {'unauthenticated': {401: {'model': schemas.ErrorDetailFlat, 'description': 'Unauthorized: User not authenticated.'}}}