function Teacher(){
    const [user, setUser] = React.useState([]);
    const getUser = () => {
        axios.get('/users_details').then((result) => {
            console.log(result.data)
            setUser(result.data);
        })
    }
    React.useEffect(() =>{
        getUser();}
        , [] 
        )
        return (

            <div>
                <div>{user.email}</div>
                <div>{user.phone}</div>

                          
            </div>
        );
}
ReactDOM.render(<Teacher/>, document.getElementById('teacher'))