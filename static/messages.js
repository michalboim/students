function Messages(props){
    return <div>
        {props.messages.map((message)=>
            <div>{message}</div>)}
    </div>
}
function getData(){axios.get('/messages').then(response=>{
    let message=response.data;
    ReactDOM.render(<Messages messages={message}/>, document.getElementById('messages'))
} 
    )

}
getData()
setInterval(getData,3000)