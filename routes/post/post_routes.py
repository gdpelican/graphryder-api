from routes.post.post_getter import *
from routes.post.post_aggregations import *


def add_comment_routes(api):
    # Getter
    # Multiple
    api.add_resource(GetPosts, '/posts')
    api.add_resource(GetPostsLatest, '/posts/latest')
    api.add_resource(GetPostsByAuthor, '/posts/author/<int:author_id>')
    api.add_resource(GetPostsOnPost, '/posts/post/<int:post_id>')
    api.add_resource(GetPostsOnComment, '/posts/comment/<int:comment_id>')
    # Simple
    api.add_resource(GetPost, '/post/<int:post_id>')
    api.add_resource(GetPostHydrate, '/post/hydrate/<int:post_id>')

    # Count
    api.add_resource(CountAllPosts, '/posts/count/')
    api.add_resource(CountPostsByAuthor, '/posts/count/author/<int:author_id>')
    api.add_resource(CountPostsByTimestamp, '/posts/count/timestamp')
