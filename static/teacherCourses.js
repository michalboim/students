function TeacherCourses(){
    
    const [Data, setData]= React.useState([]);
    const [noCourses, setNoCourses] = React.useState('');
    const [courses, setCourses] = React.useState([]);
    const [coursesInfo, setCoursesInfo] = React.useState([]);
    const [studentsInfo, setStudentsInfo] = React.useState([]);
    const [students, setStudents] = React.useState('');
    const [className, setClassName] = React.useState([]);
    const [statistics, setStatistics] = React.useState([]);
    
    const getFun=(event)=>{
        event.preventDefault();
        let id=event.target.value;
        let name=event.target.name;
        Data.forEach(function(item, index){
            if (item.id==id){
                if (name=='information'){
                    setCoursesInfo(item)
                    setStudentsInfo([])
                    setStudents('')
                    setClassName([])
                    setStatistics('')
                }
                if (name=='students'){
                    setStudentsInfo(item.students)
                    setStudents(item)
                    setClassName(item.class)
                    setCoursesInfo('')
                    setStatistics('')
                }
                if (name=='statistics'){
                    setStatistics(item)
                    setStudentsInfo([])
                    setStudents('')
                    setClassName([])
                    setCoursesInfo('')
                }
            }
        })

    }
    const getTeacherCourses = () => {
        axios.get('/users_details').then((result) => {
            setNoCourses(result.data.no_courses)
            setCourses(result.data.courses)
        })        
    }
    
    const getData=()=>{
        axios.get(`/courses_details`).then((result)=>{
            setData(result.data)
        })
    }
    React.useEffect(() =>{
        getTeacherCourses();
        getData();
    }, [] 
        )
        return (
            <div class='course_information'>
                <div class='courses_title'>Courses:</div>
                <div class="t_no_courses">{noCourses}</div>
                <div class="teacher_courses" >                       
                {courses.map((course)=>
                    <div class="t_course">
                        <div class="t_course_name">{course[1]}</div>
                        <div class="teacher_nav">                 
                            <button onClick={getFun} name='information' value={course[0]}>Information</button>
                            <button onClick={getFun} name='students' value={course[0]}>Students</button>
                            <button><a href={"/updeat_grade/"+course[0]}>Update Grade</a></button> 
                            <button onClick={getFun} name='statistics' value={course[0]}>Statistics</button>
                            <button><a href={"/attendance/"+course[0]}>Mark Attendance</a></button>
                        </div>   
                    </div>
                    )}                        
                </div>                
                <div class='t_course_info'>
                    <div class='t_course_title'>{coursesInfo.course_name} </div>
                    <div class='t_course_details'>
                        <div>{coursesInfo.start}</div>
                        <div>{coursesInfo.line}</div>
                        <div>{coursesInfo.day} </div>
                        <div>{coursesInfo.line}</div>
                        <div>{coursesInfo.time}</div>
                    </div>
                </div>
                <div class='t_students_info'>
                    <div>
                        <div class='t_course_title'>{students.students_title}</div>                        
                        <div class='t_course_title'> {students.no_students}</div>
                    </div>
                    <div class='students_grid'>
                        <div class={className[0]}>{students.title_name}</div>
                        <div class={className[0]}>{students.title_email}</div>
                        <div class={className[0]}>{students.title_phone}</div>
                        <div class={className[0]}>{students.title_grade}</div>
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
                <div class='t_statistics'>
                    <div class='mean_grades'>
                        <div class='t_course_title'>{statistics.mean_grades_title} {statistics.no_students}</div>
                        <div >{statistics.mean_grades} </div>
                    </div>
                    <div class='mean_grades'>
                        <div class='t_course_title'>{statistics.average_attend_title}</div>
                        <div >{statistics.average_attend} </div>
                    </div>
                </div>
            </div>    
        );
}
ReactDOM.render(<TeacherCourses/>, document.getElementById('teacher_courses'))