from rest_framework import serializers
from .models import User, Test, Question, Option, Submission

# ── 2. Register serializer (for creating a new user) ──────
class RegisterSerializer(serializers.ModelSerializer):
    # write_only=True → password goes IN but never comes back out
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES,required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'password', 'role', 'first_name', 'last_name']

    def create(self, validated_data):
        # Override create() — like method overriding in OOP
        # We MUST use create_user() so password gets hashed
        return User.objects.create_user(**validated_data)


# ── 1. User serializer (read-only, for showing user info) ──
class UserSerializer(serializers.ModelSerializer):
    # ModelSerializer = inheritance from DRF base class
    # Meta inner class = tells it WHICH model and WHICH fields
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'role']

#My code
class TestSerializer(serializers.ModelSerializer):
    # questions = QuestionSerializer(many=True)

    class Meta:
        model = Test
        fields = ['id', 'title', 'time_limit', 'is_published', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    # def create(self, validated_data):
    #     # Extract the nested questions data
    #     questions_data = validated_data.pop('questions')
        
    #     # Create the main Test object
    #     test = Test.objects.create(**validated_data)

    #     # Iterate through questions
    #     for q_data in questions_data:
    #         # Safely pop options (defaults to an empty list if not provided)
    #         options_data = q_data.pop('options', [])
            
    #         # Create the Question
    #         question = Question.objects.create(test=test, **q_data)
            
    #         # Create Options only if they exist (e.g., for 'mcq' types)
    #         for opt_data in options_data:
    #             Option.objects.create(question=question, **opt_data)

    #     return test

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        # Note: 'test' is the foreign key field. Passing a test ID here links them!
        fields = ['id', 'test', 'text', 'question_type', 'marks', 'options']

    def create(self, validated_data):
        # 1. Pop the options data safely (defaults to empty list for text questions)
        options_data = validated_data.pop('options', [])
        
        # 2. Create the Question linked to the Test
        question = Question.objects.create(**validated_data)
        
        # 3. Create the Options (if any exist)
        for opt_data in options_data:
            Option.objects.create(question=question, **opt_data)
            
        return question
    
    # --- STUDENT SERIALIZERS (Read-Only & Safe) ---

class StudentOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text'] # CRITICAL: 'is_correct' is intentionally left out!

class StudentQuestionSerializer(serializers.ModelSerializer):
    options = StudentOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'marks', 'options']

class StudentTestSerializer(serializers.ModelSerializer):
    # This automatically fetches all related questions because we set 
    # related_name='questions' in the Question model earlier!
    questions = StudentQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'title', 'time_limit', 'created_at', 'questions']

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'student', 'test', 'score', 'submitted_at']
        # The student only sends the 'test' ID. Everything else is read-only.
        read_only_fields = ['student', 'score', 'submitted_at']