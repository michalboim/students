function Admin(){
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
            <div className='hello_admin'>
                <div>Hello {user.name}- what do you want to do?</div>
            </div>
        );
}
ReactDOM.render(<Admin/>, document.getElementById('admin'))