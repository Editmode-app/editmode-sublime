import sublime, sublime_plugin, urllib, urllib.request, json

class InsertContentCommand(sublime_plugin.TextCommand):

  # To do:
  # Threading
  # Getting 
  # Warning if user accidentally hits the shortcut twice and tries to re-send the resulting snippet

  def run(self, edit):

    # Load settings
    settings = sublime.load_settings("em.sublime-settings")

    # Get variables from settings

    urls = sublime.active_window().active_view().settings().get('em_urls', settings.get("em_urls"))
    em_create_url = urls['create'] 

    authentication_token = sublime.active_window().active_view().settings().get('em_authentication_token', settings.get("em_authentication_token"))

    default_snippet_template = sublime.active_window().active_view().settings().get('em_default_snippet_template', settings.get("em_default_snippet_template"))
    snippet_templates = sublime.active_window().active_view().settings().get('em_snippet_templates', settings.get("em_snippet_templates"))
    snippet_template = snippet_templates[default_snippet_template]

    # Get selected text
    selections = self.view.sel()

    # The following code needs to be made threadsafe
    for selection in selections:

      # Get selected text
      content = self.view.substr(selection)

      data = {
          "bit" : {
              "content" : content
          },
          "authentication_token" : authentication_token
      }

      # Urllib only accepts encoded data
      params = json.dumps(data).encode('utf8')

      request = urllib.request.Request(
        em_create_url, 
        data=params, 
        headers={'Content-Type': 'application/json','User-Agent': 'Mozilla/5.0' }
      )

      try:
        response = urllib.request.urlopen(request)
        response_as_string = response.read().decode('utf8')
        response_as_json = json.loads(response_as_string)

        bit_info = response_as_json["bit"]
        
        bit_identifier = bit_info['identifier']
        bit_content = bit_info['content']

        shortened_original_content = bit_content[:10] + (bit_content[10:] and '..')

        replacement_text = snippet_template.replace("{identifier}", bit_identifier)
        replacement_text = replacement_text.replace("{label}", shortened_original_content)

        # Make the replacement
        self.view.replace(edit, selection, replacement_text )

      except urllib.error.HTTPError as e:

        response_as_string = e.read().decode('utf8')
        response_as_json = json.loads(response_as_string)
        message = response_as_json['message']

        sublime.error_message(message)


