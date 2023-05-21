function HomeCourses(){

    const [courses, setCourses] = React.useState([]);
    const [isShown, setIsShown] = React.useState(false);
    const [courseIndex, setCourseIndex] = React.useState(0);
    const [showCourse, setShowCourse] = React.useState({});
    
    const getCourses = () => {
        axios.get('/published_courses').then((result) =>{
            setCourses(result.data);
            setShowCourse(result.data[0]);
            console.log(courseIndex);
        })  
    }
    
        const goBack = () =>{
        setCourseIndex(courseIndex => courseIndex - 1)
        if (courseIndex <= 0)
        {setCourseIndex(courseIndex => courseIndex = courses.length-1)};
        console.log(courseIndex);
        setShowCourse(courses[courseIndex]);
        }
        
        const goForward = () => {  
            setCourseIndex(courseIndex => courseIndex+1)
            if (courseIndex == courses.length-1)
            {setCourseIndex(courseIndex => courseIndex = 0)};
            console.log(courseIndex);
            setShowCourse(courses[courseIndex]);
            }
        const change = (event) =>{
            event.target.style.backgroundImage = "none";
        }
    React.useEffect(() =>{
        getCourses();
        }
        , []
        )
        return(
            <div class='home_courses'>
                <div class='back'>
                   <button onClick={goBack} >Back</button> 
                </div>
                <div class='one_course' style={{backgroundImage:'url("/static/images/'+showCourse.picture+'")'}}
                onMouseEnter = {() => setIsShown(true)}
                onMouseLeave = {() => setIsShown(false)}>
                    <div class='course_name_home'>{showCourse.name}</div>
                    {isShown && (
                    <div class='course_desc_home'>{showCourse.description}</div>
                )}
                </div>
                <div class='forward'>
                    <button onClick={goForward}>Forward</button> 
                </div>   
            </div>

            );


}
const root = ReactDOM.createRoot(document.getElementById('courses'));
root.render(<HomeCourses />)