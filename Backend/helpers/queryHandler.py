class QueryHandler:
    '''
    Ticket Query is to return queryset on the basis of user role
    '''
    def __init__(self, query, request):
        self.query = query
        self.user = request.user

    def get_query(self):
        if not self.user.is_authenticated:
            return self.query.none()
        if self.user.role.lower() == "user":
            return self.query.filter(user=self.user)
        elif self.user.role.lower() == "admin":
            return self.query.all()
        return self.query.none()
