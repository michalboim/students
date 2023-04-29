function TeacherCourses(){
    const [noCourses, setNoCourses] = React.useState([]);
    const [courses, setCourses] = React.useState([]);
    const [coursesInfo, setCoursesInfo] = React.useState([]);
    const send=(event)=>{
        event.preventDefault();
        let id=event.target.value
        axios.get(`/course_details/${id}`).then((result)=>{
            setCoursesInfo(result.data)
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
                                <button onClick={send} value={course[0]}>Information</button>
                                <a href={"/attendance/"+course[0]}>Attendance</a>
                            </div>   
                        </div>
                        )}                        
                    </div>                
                </div>
                <div class='t_course_info'>
                    <div class='t_course_title'>{coursesInfo.course_name} {coursesInfo.title}</div>
                    <div>{coursesInfo.start} {coursesInfo.line} </div>
                    <div>{coursesInfo.day} {coursesInfo.line} </div>
                    <div>{coursesInfo.time} {coursesInfo.line} </div>
                </div>
            </div>    
        );
}
ReactDOM.render(<TeacherCourses/>, document.getElementById('teacher_courses'))