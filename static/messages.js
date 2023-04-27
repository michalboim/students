function AddMessagesForm(){

    const handleSubmit=(event)=>{
        event.preventDefault();
        const newMessage=event.target.elements.message.value;
        axios.post("/add", {message:newMessage}).then(
            response=>console.log(response.data)
        )
    }
    return (
        <form onSubmit={handleSubmit}>
            <input type='text' name='message'/>
            <input type='submit' value='add'/>
        </form>
    )
}

function Messages(props){

    const [messages, setMessages]=React.useState([])

    const getData=()=>{axios.get('/messages').then(response=>{
        setMessages(response.data);
    })
    }

    React.useEffect(()=>{
        getData(); //קריאה לפונצקיה של המידע בפעם הראשונה ע"מ שלא יהיה דיליי
        setInterval(getData,props.interval);
    }, []
    )
    return <div>
        {messages.map((message)=>
            <div>{message}</div>)}
    </div>
}

ReactDOM.render(<Messages start={''} interval={3000}/>, document.getElementById('messages'))
ReactDOM.render(<AddMessagesForm />, document.getElementById('add'))

{user.courses.map((course)=>
    {course.map((c)=>
        <div class="t_course_name">{c}</div>)}
    )} 