function TeacherCourses(){
    const [noCourses, setNoCourses] = React.useState('');
    const [courses, setCourses] = React.useState([]);
    const [coursesInfo, setCoursesInfo] = React.useState([]);
    const [studentsInfo, setStudentsInfo] = React.useState([]);
    const [students, setStudents] = React.useState('');
    const [className, setClassName] = React.useState([]);
    
    const courseInformation=(event)=>{
        event.preventDefault();
        let id=event.target.value
        axios.get(`/course_details/${id}`).then((result)=>{
            console.log(result.data)
            setCoursesInfo(result.data)
            setStudentsInfo([])
            setStudents('')
            setClassName([])
        })
    }
    const studentInformation=(event)=>{
        event.preventDefault();
        let id=event.target.value
        axios.get(`/course_details/${id}`).then((result)=>{
            console.log(result.data.students)
            setStudentsInfo(result.data.students)
            setStudents(result.data)
            setClassName(result.data.class)
            setCoursesInfo('')
        })
    }
    const getTeacherCourses = () => {
        axios.get('/users_details').then((result) => {
            setNoCourses(result.data.no_courses)
            setCourses(result.data.courses)
            
        })        
    }
    React.useEffect(() =>{
        getTeacherCourses();}
        , [] 
        )
        return (
            <div >
                <div class="t_nav">
                    <div>Courses:</div>
                    <div class="t_no_courses">{noCourses}</div>
                    <div class="teacher_courses" >                       
                    {courses.map((course)=>
                        <div class="t_course">
                            <div class="t_course_name">{course[1]}</div>
                            <div class="teacher_nav">
                                <button onClick={courseInformation} name='course_id' value={course[0]}>Information</button>
                                <button onClick={studentInformation} value={course[0]}>Students</button> 
                                <button><a href={"/attendance/"+course[0]}>Attendance</a></button>    
                            </div>   
                        </div>
                        )}                        
                    </div>                
                </div>
                <div class='t_course_info'>
                    <div class='t_course_title'>{coursesInfo.course_name} {coursesInfo.info_title}</div>
                    <div>{coursesInfo.start} {coursesInfo.line} </div>
                    <div>{coursesInfo.day} {coursesInfo.line} </div>
                    <div>{coursesInfo.time} {coursesInfo.line} </div>
                </div>
                <div class='t_students_info'>
                    <div >
                        <div class='t_course_title'> {students.students_title}</div>
                        <div class='t_no_courses'> {students.no_students}</div>
                    </div>
                    <div class='mean_grades'> {students.mean}</div>
                    <div class='students_grid'>
                        <div class={className[0]}>{students.name}</div>
                        <div class={className[0]}>{students.email}</div>
                        <div class={className[0]}>{students.phone}</div>
                        <div class={className[0]}>{students.grade}</div>
                        <div class='students_grid_name'>
                        {studentsInfo.map((student)=>    
                                <div>{student.name}</div>                                
                            )}
                        </div> 
                        <div class={className[1]}>
                        {studentsInfo.map((student)=>    
                                <div>{student.email}</div>                                
                            )}
                        </div> 
                        <div class={className[2]}>
                        {studentsInfo.map((student)=>    
                                <div>{student.phone}</div>                                
                            )}
                        </div> 
                        <div class={className[3]}>
                        {studentsInfo.map((student)=>    
                                <div>{student.grade}</div>                                
                            )}
                        </div> 
                    </div>
                </div> 
            </div>    
        );
}
ReactDOM.render(<TeacherCourses/>, document.getElementById('teacher_courses'))