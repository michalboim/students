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

ReactDOM.render(<Messages start={''} interval={5000}/>, document.getElementById('messages'))


