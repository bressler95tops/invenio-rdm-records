# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Community Inclusion Service."""

from invenio_records_resources.services import Service
from invenio_requests import current_requests_service
from invenio_search.engine import dsl
from invenio_pidstore.errors import PIDUnregistered  # <--- CRITICAL IMPORT


class RecordRequestsService(Service):
    """Service for records' requests.

    The RDM Requests service wraps some operations of the generic requests service,
    implementing RDM business logic.
    """

    @property
    def record_cls(self):
        """Factory for creating a record class."""
        return self.config.request_record_cls

    def search(
        self,
        identity,
        record_pid,
        params=None,
        search_preference=None,
        expand=False,
        extra_filter=None,
        **kwargs,
    ):
        """Search for record's requests."""
        try:
            record = self.record_cls.pid.resolve(record_pid)
            self.require_permission(identity, "read", record=record)
        except PIDUnregistered:
            # We return a successful 'empty' response. 
            # This prevents the 'Object instead of String' React crash.
            return self.result_list(
                self,
                identity,
                {"hits": {"hits": [], "total": {"value": 0}}},
                params=params,
            )

        search_filter = dsl.query.Bool(
            "must",
            must=[
                dsl.Q("term", **{"topic.record": record_pid}),
            ],
        )
        if extra_filter is not None:
            search_filter = search_filter & extra_filter
        return current_requests_service.search(
            identity,
            params=params,
            search_preference=search_preference,
            expand=expand,
            extra_filter=search_filter,
            **kwargs,
        )
