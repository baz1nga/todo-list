import json
import graphene
from django.middleware.csrf import CsrfViewMiddleware

from backend.todo_list.schema import Query, Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)


class CustomCsrfMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if getattr(request, 'csrf_processing_done', False):
            return None
        if getattr(callback, 'csrf_exempt', False):
            return None
        try:
            body = request.body.decode('utf-8')
            body = json.loads(body)
        except (TypeError, ValueError, UnicodeDecodeError):
            return super(CustomCsrfMiddleware, self).process_view(
                request,
                callback,
                callback_args,
                callback_kwargs,
            )
        if isinstance(body, list):
            for query in body:
                if 'mutation' in query:
                    break
            else:
                return self._accept(request)
        else:
            if 'query' in body and 'mutation' not in body:
                return self._accept(request)
        return super(CustomCsrfMiddleware, self).process_view(
            request,
            callback,
            callback_args,
            callback_kwargs,
        )
