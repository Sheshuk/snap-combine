def setId(id: str):
    def _f(data):
        data.id=id
        return data
    return _f
