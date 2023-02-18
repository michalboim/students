class Student:
    def __init__(self, tid, name, email, phone ) -> None:
        self.tid=tid
        self.name=name
        self.email=email
        self.phone=phone
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

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

class Teacher:
    def __init__(self, tid, name, email, phone ) -> None:
        self.tid=tid
        self.name=name
        self.email=email
        self.phone=phone
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name
    
