"""
Student Page Performance Optimization - Pagination and Query Optimization Module
Purpose: Provides utilities for fast loading of student data with pagination
"""

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Prefetch
from django.http import JsonResponse
import json


class StudentPaginator:
    """Handles pagination for student pages with AJAX support"""
    
    ITEMS_PER_PAGE = 15  # Visible items per page
    MAX_ITEMS_PER_PAGE = 50  # Maximum items to load
    
    @staticmethod
    def paginate_queryset(queryset, page=1, items_per_page=None):
        """
        Paginate a queryset efficiently
        
        Args:
            queryset: Django queryset to paginate
            page: Page number (default: 1)
            items_per_page: Items per page (default: ITEMS_PER_PAGE)
        
        Returns:
            dict with paginated data and metadata
        """
        if items_per_page is None:
            items_per_page = StudentPaginator.ITEMS_PER_PAGE
        
        items_per_page = min(items_per_page, StudentPaginator.MAX_ITEMS_PER_PAGE)
        
        paginator = Paginator(queryset, items_per_page)
        
        try:
            page_obj = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            page_obj = paginator.page(1)
        
        return {
            'items': page_obj.object_list,
            'page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
        }
    
    @staticmethod
    def paginate_ajax(queryset, page=1, serializer=None, items_per_page=None):
        """
        Return paginated data as JSON for AJAX requests
        
        Args:
            queryset: Django queryset
            page: Page number
            serializer: Function to serialize items to dict
            items_per_page: Items per page
        
        Returns:
            JsonResponse with paginated data
        """
        paginated = StudentPaginator.paginate_queryset(queryset, page, items_per_page)
        
        items = paginated['items']
        if serializer:
            items = [serializer(item) for item in items]
        else:
            items = [{'id': item.id, 'name': str(item)} for item in items]
        
        return JsonResponse({
            'success': True,
            'items': items,
            'page': paginated['page'],
            'has_next': paginated['has_next'],
            'has_previous': paginated['has_previous'],
            'total_pages': paginated['total_pages'],
            'total_items': paginated['total_items'],
        })


class QueryOptimizer:
    """Optimizes Django ORM queries to prevent N+1 problems"""
    
    @staticmethod
    def optimize_announcements(queryset):
        """Optimize announcements query"""
        return queryset.select_related('created_by').defer(
            'description_long'
        ).only(
            'id', 'title', 'description', 'audience', 'expires_at', 'created_at', 'created_by__first_name'
        )
    
    @staticmethod
    def optimize_assignments(queryset):
        """Optimize assignments query with prefetch"""
        return queryset.select_related('subject', 'subject__course').prefetch_related(
            'assignmentsubmission_set'
        ).defer(
            'description_long', 'subject__description'
        ).only(
            'id', 'title', 'subject', 'due_date', 'created_at', 'max_marks'
        )
    
    @staticmethod
    def optimize_materials(queryset):
        """Optimize study materials query"""
        return queryset.select_related('subject', 'subject__course').defer(
            'description_long', 'subject__description'
        ).only(
            'id', 'title', 'subject', 'created_at', 'file', 'file_type'
        )
    
    @staticmethod
    def optimize_notifications(queryset):
        """Optimize notifications query"""
        return queryset.select_related('student', 'student__admin').defer(
            'message_long'
        )
    
    @staticmethod
    def optimize_cloud_files(queryset):
        """Optimize cloud storage files query"""
        return queryset.only(
            'id', 'student', 'file', 'category', 'created_at', 'file_size'
        )
    
    @staticmethod
    def optimize_feedback(queryset):
        """Optimize feedback query"""
        return queryset.only(
            'id', 'student', 'subject', 'rating', 'message', 'created_at'
        )
    
    @staticmethod
    def optimize_leave_history(queryset):
        """Optimize leave history query"""
        return queryset.select_related('student', 'student__admin').defer(
            'reason_long'
        ).only(
            'id', 'student', 'start_date', 'end_date', 'status', 'created_at'
        )


# Cache keys for frequently accessed data
CACHE_KEYS = {
    'announcements': 'student_announcements_',
    'assignments': 'student_assignments_',
    'materials': 'student_materials_',
    'notifications': 'student_notifications_',
    'cloud_files': 'student_cloud_files_',
}
