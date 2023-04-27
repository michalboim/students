function Teacher(){
    const [user, setUser] = React.useState([]);
    const [courses, setCourses] = React.useState([]);
    const [coursesInfo, setCoursesInfo] = React.useState([]);
    const send=(event)=>{
        event.preventDefault();
        let courseId=event.target.form.elements.course_id.value;
        axios.get(`/course_details/${courseId}`).then((result)=>{
            console.log(result.data)
            setCoursesInfo(result.data)
        })
    }
    const getUser = () => {
        axios.get('/users_details').then((result) => {
            console.log(result.data);
            setUser(result.data);
            setCourses(result.data.courses)
        })        
    }
    let link1='/teacher_info_update/'+(user.id);
    React.useEffect(() =>{
        getUser();}
        , [] 
        )
        return (
            <div class="teacher_profile">
                <div class="information">
                    <div class='t_info'>
                        <div>{user.email}</div>
                        <div>{user.phone}</div>
                        <div ><a href={link1}>Update Information</a></div>                         
                    </div>
                </div>
                <div class="t_nav">
                    <div>Courses:</div>
                    <div class="t_no_courses">{user.no_courses}</div>
                    <div class="teacher_courses" >                       
                    {courses.map((course)=>
                        <div class="t_course">
                            <div class="t_course_name">{course[1]}</div>
                            <div class="teacher_nav">
                                <form>
                                    <input type='hidden' name='course_id' value={course[0]} />
                                    <input type='submit' onClick={send} value='Information'/>
                                </form>
                                <a href=''>Attendance</a>
                            </div>   
                        </div>
                        )}                        
                    </div>                
                </div>
                <div>
                    <div>{coursesInfo.course_name} {coursesInfo.title}</div>
                    <div>{coursesInfo.day}</div>
                    <div>{coursesInfo.start}</div>
                    <div>{coursesInfo.time}</div>
                </div>
            </div>    
        );
}
ReactDOM.render(<Teacher/>, document.getElementById('teacher'))