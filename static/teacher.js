function Teacher(){
    const [user, setUser] = React.useState([]);
    const getUser = () => {
        axios.get('/users_details').then((result) => {
            console.log(result.data)
            setUser(result.data);
        })        
    }
    let link='/teacher_info_update/'+(user.id);
    console.log(link)
    React.useEffect(() =>{
        getUser();}
        , [] 
        )
        return (

            <div class='t_info'>
                <div>{user.email}</div>
                <div>{user.phone}</div>
                {/* <a herf={link}>Update</a>                          */}
            </div>
        );
}
ReactDOM.render(<Teacher/>, document.getElementById('teacher'))