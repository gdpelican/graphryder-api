import psutil
import time
import json
from flask_restful import Resource, reqparse
from routes.utils import makeResponse
from connector.redisgraph import query_redisgraph


class Info(Resource):
    def get(self):
        # todo change status
        response = {"status": "ok", "version": "0000000000000", "percentRamUsage": psutil.virtual_memory()[2], "percentDiskUsage": psutil.disk_usage('/')[3]}
        req = "MATCH (n) RETURN max(n.timestamp) AS version"
        result = query_redisgraph(req)
        try:
            response['version'] = result.single()['version']
        except ResultError:
            return makeResponse("ERROR : Cannot load latest timestamp", 204)

        return makeResponse(response, 200)


class Status(Resource):
    def get(self):
        elementType = ['user', 'post', 'comment', 'annotation', 'tag']
        labels = ['Users', 'Posts', 'Comments', 'Annotations', 'Tags']
        data = []
        for t in elementType:
            req = "MATCH (e: "+t+")--() RETURN count(distinct e) as nb"
            result = query_redisgraph(req)
            for record in result:
                data.append(record['nb'])
        return makeResponse({'labels': labels, 'data': [data]}, 200)


class GetContentNotTagged(Resource):
    def get(self):
        req = "MATCH (p:post) WHERE NOT (p)<-[:ANNOTATES]- (: annotation) RETURN p.post_id AS post_id,p.label AS label, p.timestamp AS timestamp ORDER BY timestamp DESC"
        result = query_redisgraph(req)
        posts = []
        for record in result:
            posts.append({'post_id': record['post_id'], "label": record['label'], "timestamp": record['timestamp']})

        req = "MATCH (c:comment) WHERE NOT (c)<-[:ANNOTATES]- (: annotation) RETURN c.comment_id AS comment_id, c.label AS label, c.timestamp AS timestamp ORDER BY timestamp DESC"
        result = query_redisgraph(req)
        comments = []
        for record in result:
            comments.append({'comment_id': record['comment_id'], "label": record['label'], "timestamp": record['timestamp']})

        return makeResponse({'posts': posts, "comments": comments}, 200)
