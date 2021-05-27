def setId(id: str):
    """ Processing :term:`step`, 
    setting given id to all the passing data objects.

    Args:
        id: client id to be set.

    :Input:
        data (object)
    :Output:
        data with set id (:code:`data.id = id`)
    """

    def _f(data):
        data.id=id
        return data
    return _f
