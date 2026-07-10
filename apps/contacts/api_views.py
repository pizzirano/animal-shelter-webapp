"""
API Views for Contact app
"""
from rest_framework import viewsets, status # pyright: ignore[reportMissingImports]
from rest_framework.response import Response # pyright: ignore[reportMissingImports]
from rest_framework.decorators import action # pyright: ignore[reportMissingImports]
from .models import ContactMessage
from .serializers import ContactMessageSerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for contact messages.

    list: List messages (staff only)
    create: Send a new message
    retrieve: Message detail (staff only)
    """
    queryset = ContactMessage.objects.all().select_related('dog').order_by('-created_at')
    serializer_class = ContactMessageSerializer
    http_method_names = ['get', 'post', 'head', 'options']  # GET and POST only
    
    def get_queryset(self):
        """Restrict the view to staff only."""
        if self.request.user.is_staff:
            return self.queryset
        return ContactMessage.objects.none()
    
    def list(self, request, *args, **kwargs):
        """List messages - staff only."""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Non hai i permessi per visualizzare questa risorsa.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """Message detail - staff only."""
        if not request.user.is_staff:
            return Response(
                {'detail': 'Non hai i permessi per visualizzare questa risorsa.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Create a new message - public."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                'message': 'Messaggio inviato con successo! Ti risponderemo al più presto.',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Count unread messages - staff only.
        GET /api/v1/contacts/unread/ or API_URL/contacts/unread/ depending on config in .env
        """
        if not request.user.is_staff:
            return Response(
                {'detail': 'Non autorizzato.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        unread_count = ContactMessage.objects.filter(is_read=False).count()
        return Response({'unread_count': unread_count})
