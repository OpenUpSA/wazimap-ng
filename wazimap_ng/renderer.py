import json
from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # print(data, renderer_context)
        response = renderer_context.get('response')

        if response.status_code >= 400:
            type = data.get('detail', None).code
            data = {
                "error": {
                    "message": data,
                    "type": type,
                    "code": response.status_code,
                }
            }

        return super().render(data, accepted_media_type, renderer_context)

    # def render(self, data, accepted_media_type=None, renderer_context=None):
    #     """
    #     Render `data` into JSON, returning a bytestring.
    #     """
    #     if data is None:
    #         return bytes()

    #     renderer_context = renderer_context or {}
    #     indent = self.get_indent(accepted_media_type, renderer_context)

    #     if indent is None:
    #         separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
    #     else:
    #         separators = INDENT_SEPARATORS

    #     ret = json.dumps(
    #         data, cls=self.encoder_class,
    #         indent=indent, ensure_ascii=self.ensure_ascii,
    #         allow_nan=not self.strict, separators=separators
    #     )

    #     # On python 2.x json.dumps() returns bytestrings if ensure_ascii=True,
    #     # but if ensure_ascii=False, the return type is underspecified,
    #     # and may (or may not) be unicode.
    #     # On python 3.x json.dumps() returns unicode strings.
    #     if isinstance(ret, six.text_type):
    #         # We always fully escape \u2028 and \u2029 to ensure we output JSON
    #         # that is a strict javascript subset. If bytes were returned
    #         # by json.dumps() then we don't have these characters in any case.
    #         # See: http://timelessrepo.com/json-isnt-a-javascript-subset
    #         ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    #         return bytes(ret.encode('utf-8'))
    #     return ret
