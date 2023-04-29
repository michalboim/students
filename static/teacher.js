function Teacher(){
    const [user, setUser] = React.useState([]);
    const getUser = () => {
        axios.get('/users_details').then((result) => {
            setUser(result.data);
        })        
    }
    React.useEffect(() =>{
        getUser();}
        , [] 
        )
        return (
            <div class='t_info'>
                <div>{user.email}</div>
                <div>{user.phone}</div>
                <div ><a href={'/teacher_info_update/'+user.id}>Update Information</a></div>                         
            </div>        
        );
}
ReactDOM.render(<Teacher/>, document.getElementById('teacher'))