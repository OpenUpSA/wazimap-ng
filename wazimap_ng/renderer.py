from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):

    def error_data(self, data, type, code):
        return dict(
            error={
                "message": data,
                "type": type,
                "code": code
            }
        )

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')

        if response.status_code >= 400:
            type = data.get('detail', None)
            type = getattr(type, 'code', None)
            data = self.error_data(data, type, response.status_code)

        return super().render(data, accepted_media_type, renderer_context)
