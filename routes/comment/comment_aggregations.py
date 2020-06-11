from flask_restful import Resource, reqparse
from connector.redisgraph import query_redisgraph
from routes.utils import addargs, makeResponse

parser = reqparse.RequestParser()


class CountAllComments(Resource):
    def get(self):
        req = "MATCH (:comment) RETURN count(*) AS nb_comments"
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_comments'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountCommentsByAuthor(Resource):
    def get(self, author_id):
        req = "MATCH (author:user {user_id : %d})-[:AUTHORSHIP]->(c:comment) RETURN count(*) AS nb_comments" % author_id
        result = query_redisgraph(req)
        try:
            return makeResponse(result.single()['nb_comments'], 200)
        except ResultError:
            return makeResponse("ERROR", 500)


class CountCommentsByTimestamp(Resource):
    def get(self):
        req = "MATCH (n:comment) RETURN n.timestamp AS timestamp ORDER BY timestamp ASC"
        req += addargs()
        result = query_redisgraph(req)
        comments = []
        count = 1
        for record in result:
            comments.append({"count": count, "timestamp": record['timestamp']})
            count += 1
        return makeResponse(comments, 200)
