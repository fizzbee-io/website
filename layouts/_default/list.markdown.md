# {{ .Title }}
{{ with .Description }}
> {{ . }}
{{ end }}
Canonical: {{ .Permalink }}{{ with .Params.source }}
Source: {{ . }}{{ end }}

{{ .RenderShortcodes }}
