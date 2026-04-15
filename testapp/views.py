from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

# --- NEW IMPORTS ADDED FOR TEST VIEWSET ---
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
# Make sure to import TestSerializer alongside your others
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer, LoginResponseSerializer, TestSerializer, QuestionSerializer, StudentTestSerializer, SubmissionSerializer
from django.contrib.auth import authenticate
from .models import Test, Question, Submission

# ── Helper: generate tokens for a user ────────────────────
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access':  str(refresh.access_token),
    }

# ══════════════════════════════════════════════════════════
# REGISTER VIEW
# ══════════════════════════════════════════════════════════
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            return Response({
                'user':   UserSerializer(user).data,
                'tokens': tokens,
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# ══════════════════════════════════════════════════════════
# LOGIN VIEW
# ══════════════════════════════════════════════════════════
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_serializer = LoginSerializer(data=request.data)
        if not login_serializer.is_valid():
            return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = login_serializer.validated_data['username']  
        password = login_serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)

        if user is not None:
            tokens = get_tokens_for_user(user)
            return Response({
                'user':   LoginResponseSerializer(user).data,
                'tokens': tokens,
            })

        return Response(
            {'error': 'Invalid username or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )


# ══════════════════════════════════════════════════════════
# TEST VIEWSET (CREATE, READ, UPDATE, DELETE TESTS)
# ══════════════════════════════════════════════════════════
class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    # This ensures a user MUST provide a valid JWT token to access this endpoint
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Check if the user is a teacher
        if self.request.user.role != 'teacher':
            raise PermissionDenied("Only users with the 'teacher' role can create tests.")
        
        # Save the test and link it to the logged-in user
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        # 1. Validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 2. Save data (triggers perform_create)
        self.perform_create(serializer)
        
        # 3. Return custom message
        return Response({
            "message": "test created successfully",
            "test_id": serializer.instance.id
        }, status=status.HTTP_201_CREATED)
    
class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # 1. Ensure user is a teacher
        if self.request.user.role != 'teacher':
            raise PermissionDenied("Only teachers can add questions.")
        
        # 2. Ensure the teacher owns the test they are adding questions to
        test = serializer.validated_data['test']
        if test.created_by != self.request.user:
            raise PermissionDenied("You can only add questions to your own tests.")
        
        # 3. Save the question
        serializer.save()

class StudentTestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Handles GET /student/tests and GET /student/tests/{id}
    """
    serializer_class = StudentTestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 1. Enforce Role: Only students can fetch tests this way
        if self.request.user.role != 'student':
            raise PermissionDenied("Only students can access the test list.")
        
        # 2. Filter: Only return tests that the teacher has actually published
        return Test.objects.filter(is_published=True)
    
class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    # @action creates a custom route: /api/submissions/start/
    @action(detail=False, methods=['post'])
    def start(self, request):
        # 1. Security Check: Only students can start tests
        if request.user.role != 'student':
            raise PermissionDenied("Only students can start a test.")

        # 2. Grab the test ID from the request
        test_id = request.data.get('test')
        if not test_id:
            return Response({"error": "test ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Verify the test exists and is actually published
        try:
            test = Test.objects.get(id=test_id, is_published=True)
        except Test.DoesNotExist:
            return Response({"error": "Test not found or not published."}, status=status.HTTP_404_NOT_FOUND)

        # 4. Create the submission (or get it if the student already started it)
        submission, created = Submission.objects.get_or_create(
            student=request.user,
            test=test
        )

        if created:
            message = "Test attempt started successfully."
            status_code = status.HTTP_201_CREATED
        else:
            message = "You have already started this test. Resuming attempt."
            status_code = status.HTTP_200_OK

        return Response({
            "message": message,
            "submission_id": submission.id,
            "test_title": test.title
        }, status=status_code)