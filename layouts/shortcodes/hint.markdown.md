**{{ default (title (default "note" (.Get "type"))) (.Get "title") }}:**
{{ trim .Inner "\r\n" }}
