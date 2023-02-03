class Student:
    def __init__(self, tid, name, email ) -> None:
        self.tid=tid
        self.name=name
        self.email=email
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

class Course:
    def __init__(self, tid, name, description, teacher_id ) -> None:
        self.tid=tid
        self.name=name
        self.description=description
        self.teacher_id=teacher_id
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

class Teacher:
    def __init__(self, tid, name, email ) -> None:
        self.tid=tid
        self.name=name
        self.email=email
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name
    
