from flask_restful import Resource, reqparse
from connector.redisgraph import query_redisgraph
from routes.utils import addargs, makeResponse

parser = reqparse.RequestParser()


class CountAllPost(Resource):
    def get(self):
        req = "MATCH (:post) RETURN count(*) AS nb_posts"
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_posts'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountPostByAuthor(Resource):
    def get(self, author_id):
        req = "MATCH (author:user {user_id : %d})-[:AUTHORSHIP]->(:post) RETURN count(*) AS nb_posts" % author_id
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_posts'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountPostsByTimestamp(Resource):
    def get(self):
        req = "MATCH (n:post) RETURN n.timestamp AS timestamp ORDER BY timestamp ASC"
        req += addargs()
        result = query_redisgraph(req)
        posts = []
        count = 1
        for record in result:
            posts.append({"count": count, "timestamp": record['timestamp']})
            count += 1
        return makeResponse(posts, 200)
