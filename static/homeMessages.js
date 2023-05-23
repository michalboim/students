function HomeMessages(){
    
    const [messages, setMessages] = React.useState([]);

    
    const getMessages = () => {
        axios.get('/home_messages').then((result) =>{
            setMessages(result.data);
        });  
    };
    

    React.useEffect(() =>{
        getMessages();
      
        }
        , []
        );
        return(
            <div class='home_messages'>
                <div class='home_message_title'>Messages:</div>
                <div class='list_messages'>
                    {messages.reverse().map((message) =>
                    <div class="one_message">{message.text}</div>
                    )}
                </div>
            </div>

            );


}
const root = ReactDOM.createRoot(document.getElementById('messages'));
root.render(<HomeMessages  />)