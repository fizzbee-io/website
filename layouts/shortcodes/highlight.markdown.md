```{{ with .Get 0 }}{{ lower . }}{{ end }}
{{ trim .Inner "\r\n" }}
```
