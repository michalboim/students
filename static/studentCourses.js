function TeacherCourses(){
    
    const [Data, setData]= React.useState([]);
    const [noCourses, setNoCourses] = React.useState('');
    const [courses, setCourses] = React.useState([]);
    const [coursesInfo, setCoursesInfo] = React.useState([]);
    const [statistics, setStatistics] = React.useState('');
    const [studentStat, setStudentStat] = React.useState('');
    const [messages, setMessages] = React.useState([]);
    const [noMessages, setNoMessages] = React.useState([]);
    
    const getFun=(event)=>{
        event.preventDefault();
        let id=event.target.value;
        let name=event.target.name;
        Data.forEach(function(item, index){
            if (item.id==id){
                if (name=='information'){
                    setCoursesInfo(item)
                    setStatistics('')
                    setStudentStat('')
                    setMessages([])
                    setNoMessages('')
                }
                if (name=='messages'){
                    setCoursesInfo('')
                    setStatistics('')
                    setStudentStat('')
                    setMessages(item.messages)
                    setNoMessages(item)
                }
                if (name=='statistics'){
                    courses.forEach(function(item,index){
                        if (item.course_id==id){
                            setStudentStat(item)
                        }
                    })
                    setStatistics(item)
                    setCoursesInfo('')
                    setMessages([])
                    setNoMessages('')
                }
            }
        })

    }
    const getStudentCourses = () => {
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
        getStudentCourses();
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
                        <div class="t_course_name">{course.course_name}</div>
                        <div class="teacher_nav">                 
                            <button onClick={getFun} name='information' value={course.course_id}>Information</button>           
                            <button onClick={getFun} name='statistics' value={course.course_id}>Statistics</button>
                            <button onClick={getFun} name='messages' value={course.course_id}>Messages</button>
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
                <div class='t_statistics'>
                    <div class='mean_grades'>
                        <div class='t_course_title'>{statistics.mean_grades_title}</div>
                        <div >{statistics.mean_grades} </div>
                        <div>{studentStat.course_grade}</div>
                    </div>
                    <div class='mean_grades'>
                        <div class='t_course_title'>{statistics.average_attend_title}</div>
                        <div >{statistics.average_attend} </div>
                        <div>{studentStat.course_attend}</div>
                    </div>
                    <div class='average_note'>{statistics.average_note}</div>
                </div>
                <div class='t_no_messages' >{noMessages.no_messages}</div>
                <div class='t_messages'>
                    <div class='t_course_title'>{noMessages.messages_title}</div>
                    {messages.map((message)=>
                    <div>{message}</div>
                    )}
                </div>
            </div>    
        );
}
ReactDOM.render(<TeacherCourses/>, document.getElementById('teacher_courses'))