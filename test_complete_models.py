"""
Test complete model system with all relationships and XOR constraint.
"""
from app.core.database import SessionLocal, drop_tables, create_tables
from app.models import User, Room, Conversation, ConversationParticipant, Message
from app.models import UserStatus, ConversationType, MessageType

print("Testing Complete Model System:...")

drop_tables()
create_tables()

db = SessionLocal()

try:
    print("\n1. Creating test data:...")

    user1 = User(email="some@test.com", username="some", password_hash="hash1")
    user2 = User(email="bobby@test.com", username="bobby", password_hash="hash2")

    room = Room(name="General", description="Main chat room", max_users=50)

    db.add_all([user1, user2, room])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)
    db.refresh(room)

    user1.current_room_id = room.id
    user2.current_room_id = room.id

    conversation = Conversation(
        room_id=room.id,
        conversation_type=ConversationType.PRIVATE,
        max_participants=2
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    participant1 = ConversationParticipant(conversation_id=conversation.id, user_id=user1.id)
    participant2 = ConversationParticipant(conversation_id=conversation.id, user_id=user2.id)
    db.add_all([participant1, participant2])
    db.commit()

    print("Test data created")

    print("\n2. Testing XOR constraint Room Message...")
    room_message = Message(
        sender_id=user1.id,
        room_id=room.id,
        conversation_id=None,
        content="Hello everyone!",
        message_type=MessageType.TEXT
    )
    db.add(room_message)
    db.commit()
    print(f"Room message: {room_message}")

    print("\n3. Testing XOR constraint Conversation Message...")
    conv_message = Message(
        sender_id=user2.id,
        room_id=None,
        conversation_id=conversation.id,
        content="Hi Some!",
        message_type=MessageType.TEXT
    )
    db.add(conv_message)
    db.commit()
    print(f"Conversation message: {conv_message}")


    print("\n4. Testing Relationships...")

    user_messages = user1.sent_messages.all()
    print(f"User1 messages: {len(user_messages)}")

    room_messages = room.room_messages.all()
    print(f"Room messages: {len(room_messages)}")

    conv_messages = conversation.messages.all()
    print(f"Conversation messages: {len(conv_messages)}")

    print(f"Room message target: {room_message.chat_target}")
    print(f"Conversation message target: {conv_message.chat_target}")

    print("\nAll tests passed!")

except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()