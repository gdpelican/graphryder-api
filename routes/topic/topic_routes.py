from routes.topic.topic_getter import *
from routes.topic.topic_aggregations import *


def add_post_routes(api):
    # Getters
    # Multiple
    api.add_resource(GetTopics, '/posts')
    api.add_resource(GetTopicsLatest, '/posts/latest')
    api.add_resource(GetTopicsByType, '/posts/type/<string:post_type>')
    api.add_resource(GetTopicsByAuthor, '/posts/author/<int:author_id>')
    # Single
    api.add_resource(GetTopic, '/post/<int:post_id>')
    api.add_resource(GetTopicHydrate, '/post/hydrate/<int:post_id>')
    # Distinct
    api.add_resource(GetTopicType, '/post/getType')

    # Count
    api.add_resource(CountAllTopic, '/posts/count/')
    api.add_resource(CountTopicByAuthor, '/posts/count/author/<int:author_id>')
    api.add_resource(CountTopicsByTimestamp, '/posts/count/timestamp')

    # todo GetTopicsByDate(min, max) need to have a fix time format
