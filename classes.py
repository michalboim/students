class Course:
    def __init__(self, tid, name, description, teacher_id, start, day, time ) -> None:
        self.tid=tid
        self.name=name
        self.description=description
        self.teacher_id=teacher_id
        self.start=start
        self.day=day
        self.time=time
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

class Student:
    def __init__(self, tid, name, email, phone, user_id ) -> None:
        self.tid=tid
        self.name=name
        self.email=email
        self.phone=phone
        self.user_id=user_id
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

class Teacher:
    def __init__(self, tid, name, email, phone, user_id ) -> None:
        self.tid=tid
        self.name=name
        self.email=email
        self.phone=phone
        self.user_id=user_id
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name
    
