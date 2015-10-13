<?php
include_once("../common/lib.php");


/**
 * Handle file uploads via XMLHttpRequest
 */
class qqUploadedFileXhr {
    /**
     * Save the file to the specified path
     * @return boolean TRUE on success
     */
    function save($path) {    
        $input = fopen("php://input", "r");
        $temp = tmpfile();
        $realSize = stream_copy_to_stream($input, $temp);
        fclose($input);
        
        if ($realSize != $this->getSize()){            
            return false;
        }
        
        $target = fopen($path, "w");        
        fseek($temp, 0, SEEK_SET);
        stream_copy_to_stream($temp, $target);
        fclose($target);
        
        return true;
    }
    function getName() {
        //return $_GET['qqfile'];
		/* eats : Space is not allowed. */
        return str_replace(" ", "_", $_GET['qqfile']);
    }
    function getSize() {
        if (isset($_SERVER["CONTENT_LENGTH"])){
            return (int)$_SERVER["CONTENT_LENGTH"];            
        } else {
            throw new Exception('Getting content length is not supported.');
        }      
    }   
}

/**
 * Handle file uploads via regular form post (uses the $_FILES array)
 */
class qqUploadedFileForm {  
    /**
     * Save the file to the specified path
     * @return boolean TRUE on success
     */
    function save($path) {
        if(!move_uploaded_file($_FILES['qqfile']['tmp_name'], $path)){
            return false;
        }
        return true;
    }
    function getName() {
        return $_FILES['qqfile']['name'];
    }
    function getSize() {
        return $_FILES['qqfile']['size'];
    }
}

class qqFileUploader {
    private $allowedExtensions = array();
    /* private $sizeLimit = 10485760; */
    /* private $sizeLimit = 536870912; /* 512M */
    private $sizeLimit = 1073741824; /* 1024M */
    private $file;

    private $user_info;

    function __construct(array $allowedExtensions = array(), $sizeLimit = 1073741824){
        $allowedExtensions = array_map("strtolower", $allowedExtensions);
            
        $this->allowedExtensions = $allowedExtensions;        
        $this->sizeLimit = $sizeLimit;
        
        $this->checkServerSettings();       

        if (isset($_GET['qqfile'])) {
			/* ghan : comming here. */
            $this->file = new qqUploadedFileXhr();
        } elseif (isset($_FILES['qqfile'])) {
            $this->file = new qqUploadedFileForm();
        } else {
            $this->file = false; 
        }
    }
    
    private function checkServerSettings(){        
        $postSize = $this->toBytes(ini_get('post_max_size'));
        $uploadSize = $this->toBytes(ini_get('upload_max_filesize'));        
        
        if ($postSize < $this->sizeLimit || $uploadSize < $this->sizeLimit){
            $size = max(1, $this->sizeLimit / 1024 / 1024) . 'M';             
            die("{'error':'increase post_max_size and upload_max_filesize to $size'}");    
        }        
    }
    
    private function toBytes($str){
        $val = trim($str);
        $last = strtolower($str[strlen($str)-1]);
        switch($last) {
            case 'g': $val *= 1024;
            case 'm': $val *= 1024;
            case 'k': $val *= 1024;        
        }
        return $val;
    }
    
    /**
     * Returns array('success'=>true) or array('error'=>'error message')
     */
    function handleUpload($uploadDirectory, $replaceOldFile = FALSE){
        if (!is_writable($uploadDirectory)){
            return array('error' => "Server error. Upload directory isn't writable.  CUR_DIR: " . getcwd() . " DIR: " . $uploadDirectory);
        }
        
        if (!$this->file){
            return array('error' => 'No files were uploaded.');
        }
        
        $size = $this->file->getSize();
        
        if ($size == 0) {
            return array('error' => 'File is empty');
        }
        
        if ($size > $this->sizeLimit) {
            return array('error' => 'File is too large');
        }
        
		$org_filename = $this->file->getName();
		/* ghan : split to filename and extension to support hangeul name. */
		$match_result = preg_match('/^(.*[^.])\.+([^.]*)$/', $org_filename, $m);
        //$filename = md5(uniqid());
		if ($match_result) {
			$filename = $m[1].'.';
			$ext = $m[2];
		} else {
			$filename = $org_filename;
		}

        if($this->allowedExtensions && !in_array(strtolower($ext), $this->allowedExtensions)){
            $these = implode(', ', $this->allowedExtensions);
            return array('error' => 'File has an invalid extension, it should be one of '. $these . '.');
        }
        
        if(!$replaceOldFile){
            /// don't overwrite previous files that were uploaded
            while (file_exists($uploadDirectory . $filename . $ext)) {
                $filename .= rand(10, 99);
            }
        }

		// Hide User Input form.
		//$userid = $_GET["userid"];
		
        if ($this->file->save($uploadDirectory.$filename.$ext)){
			/* post work here. */
            $csv=file_get_contents($uploadDirectory.$filename.$ext);
            // $data=;
			return array('success'=>true, 'path'=>$uploadDirectory.$filename.$ext, 'contents'=>csvToMongo($csv));
        } else {
            return array('error'=> 'Could not save uploaded file.' .
                'The upload was cancelled, or server error encountered');
        }
    }    
}

// list of valid extensions, ex. array("jpeg", "xml", "bmp")
$allowedExtensions = array("csv");
// max file size in bytes
// 1024 MB
$sizeLimit = 1024 * 1024 * 1024;

$uploader = new qqFileUploader($allowedExtensions, $sizeLimit);
$result = $uploader->handleUpload($ABS_FileUploadPath);
// to pass data through iframe you will need to encode all html tags

//echo json_encode($result, JSON_PRETTY_PRINT);
//echo htmlspecialchars(json_encode($result), ENT_NOQUOTES);

echo json_encode($result);

?>
