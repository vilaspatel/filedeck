{{/*
Expand the name of the chart.
*/}}
{{- define "content-manager.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "content-manager.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "content-manager.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "content-manager.labels" -}}
helm.sh/chart: {{ include "content-manager.chart" . }}
{{ include "content-manager.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "content-manager.selectorLabels" -}}
app.kubernetes.io/name: {{ include "content-manager.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "content-manager.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "content-manager.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Backend image
*/}}
{{- define "content-manager.backend.image" -}}
{{- with .Values.backend.image }}
{{- if .registry }}
{{- printf "%s/%s:%s" .registry .repository (.tag | default $.Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .repository (.tag | default $.Chart.AppVersion) }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Frontend image
*/}}
{{- define "content-manager.frontend.image" -}}
{{- with .Values.frontend.image }}
{{- if .registry }}
{{- printf "%s/%s:%s" .registry .repository (.tag | default $.Chart.AppVersion) }}
{{- else }}
{{- printf "%s:%s" .repository (.tag | default $.Chart.AppVersion) }}
{{- end }}
{{- end }}
{{- end }}

{{/*
PostgreSQL hostname
*/}}
{{- define "content-manager.postgresql.hostname" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "content-manager.fullname" .) }}
{{- else }}
{{- .Values.externalDatabase.host }}
{{- end }}
{{- end }}

{{/*
PostgreSQL port
*/}}
{{- define "content-manager.postgresql.port" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.primary.service.ports.postgresql | default 5432 }}
{{- else }}
{{- .Values.externalDatabase.port | default 5432 }}
{{- end }}
{{- end }}

{{/*
PostgreSQL database name
*/}}
{{- define "content-manager.postgresql.database" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.database }}
{{- else }}
{{- .Values.externalDatabase.database }}
{{- end }}
{{- end }}

{{/*
PostgreSQL username
*/}}
{{- define "content-manager.postgresql.username" -}}
{{- if .Values.postgresql.enabled }}
{{- .Values.postgresql.auth.username }}
{{- else }}
{{- .Values.externalDatabase.username }}
{{- end }}
{{- end }}

{{/*
PostgreSQL password secret name
*/}}
{{- define "content-manager.postgresql.passwordSecret" -}}
{{- if .Values.postgresql.enabled }}
{{- printf "%s-postgresql" (include "content-manager.fullname" .) }}
{{- else }}
{{- .Values.externalDatabase.passwordSecret }}
{{- end }}
{{- end }}

{{/*
PostgreSQL password secret key
*/}}
{{- define "content-manager.postgresql.passwordSecretKey" -}}
{{- if .Values.postgresql.enabled }}
{{- "password" }}
{{- else }}
{{- .Values.externalDatabase.passwordSecretKey }}
{{- end }}
{{- end }}

{{/*
Redis hostname
*/}}
{{- define "content-manager.redis.hostname" -}}
{{- if .Values.redis.enabled }}
{{- printf "%s-redis-master" (include "content-manager.fullname" .) }}
{{- else }}
{{- .Values.externalRedis.host }}
{{- end }}
{{- end }}

{{/*
Redis port
*/}}
{{- define "content-manager.redis.port" -}}
{{- if .Values.redis.enabled }}
{{- .Values.redis.master.service.ports.redis | default 6379 }}
{{- else }}
{{- .Values.externalRedis.port | default 6379 }}
{{- end }}
{{- end }} 