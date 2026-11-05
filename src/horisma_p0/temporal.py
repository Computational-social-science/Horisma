"""Explicit date precision and event semantics; no inferred delivery or coinage."""
import calendar
from datetime import date, datetime
import re

EVENT_TYPES = {'SOURCE_PUBLICATION', 'SCHEDULED_PRESENTATION', 'OCCURRENCE_CLAIM',
               'RETROSPECTIVE_ACKNOWLEDGMENT', 'SYSTEM_REVISION'}


def date_interval(spec):
    required = {'precision','value','earliest','latest','calendar','missing_reason'}
    if not isinstance(spec, dict) or set(spec) != required:
        raise ValueError('EXPLICIT_DATE_FIELDS_REQUIRED')
    precision, value = spec['precision'], spec['value']
    if precision == 'UNKNOWN':
        if any(spec[k] is not None for k in ['value','earliest','latest']) or not isinstance(spec['missing_reason'], str) or not spec['missing_reason'].strip():
            raise ValueError('UNKNOWN_DATE_REQUIRES_NULLS_AND_REASON')
        if spec['calendar'] not in {'GREGORIAN','UNRESOLVED'}:
            raise ValueError('UNSUPPORTED_CALENDAR')
        return {**spec, 'earliest':None, 'latest':None}
    if spec['calendar'] != 'GREGORIAN' or spec['missing_reason'] is not None:
        raise ValueError('EXPLICIT_CALENDAR_REQUIRED')
    if precision == 'INTERVAL':
        if value is not None:
            raise ValueError('INTERVAL_HAS_NO_EXACT_VALUE')
        if any(not isinstance(spec[k],str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',spec[k]) for k in ['earliest','latest']):
            raise ValueError('INTERVAL_REQUIRES_ISO_DAY_BOUNDS')
        lo, hi = date.fromisoformat(spec['earliest']), date.fromisoformat(spec['latest'])
    else:
        formats = {'DAY':r'\d{4}-\d{2}-\d{2}', 'MONTH':r'\d{4}-\d{2}', 'YEAR':r'\d{4}'}
        if precision not in formats or not isinstance(value,str) or not re.fullmatch(formats[precision],value):
            raise ValueError('VALUE_MUST_MATCH_DATE_PRECISION')
        if spec['earliest'] is not None or spec['latest'] is not None:
            raise ValueError('PRECISION_BOUNDS_ARE_DERIVED_NOT_USER_EXACT_DATES')
        if precision == 'DAY':
            lo = hi = date.fromisoformat(value)
        elif precision == 'MONTH':
            year, month = map(int,value.split('-'))
            lo = date(year,month,1); hi = date(year,month,calendar.monthrange(year,month)[1])
        else:
            lo = date(int(value),1,1); hi = date(int(value),12,31)
    if lo > hi:
        raise ValueError('REVERSED_DATE_INTERVAL')
    return {**spec, 'earliest':lo.isoformat(), 'latest':hi.isoformat()}


def validate_event(event):
    if not isinstance(event,dict) or not isinstance(event.get('event_type'),str):
        raise ValueError('TYPED_EVENT_REQUIRED')
    if event['event_type'] not in EVENT_TYPES:
        raise ValueError('UNKNOWN_EVENT_TYPE')
    if event['event_type'] == 'SYSTEM_REVISION':
        if set(event) != {'event_type','date','recorded_at'}:
            raise ValueError('SYSTEM_EVENT_FIELDS_REQUIRED')
        if event.get('date') is not None:
            raise ValueError('SYSTEM_TIME_IS_NOT_HISTORICAL_DATE')
        instant = datetime.fromisoformat(event['recorded_at'])
        if instant.tzinfo is None:
            raise ValueError('SYSTEM_TIME_REQUIRES_TIMEZONE')
        return {**event, 'track':'SYSTEM_REVISION'}
    if set(event) != {'event_type','date','verification','basis'}:
        raise ValueError('HISTORICAL_EVENT_FIELDS_REQUIRED')
    if event.get('verification') not in {'PROVISIONAL','REPORTED'}:
        raise ValueError('NO_VERIFIED_OCCURRENCE_WITHOUT_QUALIFIED_ADAPTER')
    if not isinstance(event.get('basis'),str) or not event['basis'].strip():
        raise ValueError('EVENT_BASIS_REQUIRED')
    tracks = {'SOURCE_PUBLICATION':'SOURCE_PUBLICATION', 'SCHEDULED_PRESENTATION':'PLANNED_EVENT',
              'OCCURRENCE_CLAIM':'OCCURRENCE_CLAIM', 'RETROSPECTIVE_ACKNOWLEDGMENT':'SOURCE_PUBLICATION'}
    return {**event, 'interval':date_interval(event['date']), 'track':tracks[event['event_type']]}
