from routes.comment.comment_getter import *
from routes.comment.comment_aggregations import *


def add_comment_routes(api):
    # Getter
    # Multiple
    api.add_resource(GetComments, '/comments')
    api.add_resource(GetCommentsByAuthor, '/comments/author/<int:author_id>')
    api.add_resource(GetCommentsOnContent, '/comments/content/<int:content_id>')
    api.add_resource(GetCommentsOnComment, '/comments/comment/<int:comment_id>')
    # Simple
    api.add_resource(GetComment, '/comment/<int:comment_id>')

    # Count
    api.add_resource(CountAllComments, '/comments/count/')
    api.add_resource(CountCommentsByAuthor, '/comments/count/author/<int:author_id>')

